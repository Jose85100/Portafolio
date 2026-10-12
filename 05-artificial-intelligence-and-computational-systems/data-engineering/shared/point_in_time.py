"""Point-in-time feature joins with availability and bitemporal controls."""
from bisect import bisect_right
from datetime import datetime, timezone


def _parse(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO-8601 timestamp string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed, parsed.tzinfo is not None and parsed.utcoffset() is not None


def _temporal_context(records, fields):
    awareness, parsed = set(), {}
    for index, record in enumerate(records):
        for field in fields:
            if field in record and record[field] not in (None, ""):
                value, aware = _parse(record[field], field)
                awareness.add(aware)
                parsed[index, field] = value.replace(tzinfo=timezone.utc) if not aware else value.astimezone(timezone.utc)
    if len(awareness) > 1:
        raise ValueError("mixed naive and timezone-aware timestamps are forbidden")
    # Legacy timestamp strings without offsets are accepted only as an all-naive
    # batch and are explicitly interpreted as UTC.
    return parsed, awareness


def asof_join(events, features, key="entity_id", event_time="decision_at",
              feature_time="available_at", feature_names=None,
              recorded_at="recorded_at", valid_from="valid_from", valid_to="valid_to",
              system_as_of=None):
    """Join the latest usable feature without temporal leakage.

    ``available_at`` is the availability clock. Optional ``recorded_at`` is
    the system clock: retroactive corrections are invisible before recording.
    Optional validity fields define ``[valid_from, valid_to)``. Per-entity
    binary-search indexes avoid a linear candidate scan for every event.
    """
    event_records, feature_records = list(events), list(features)
    all_records = event_records + feature_records
    parsed, awareness = _temporal_context(
        all_records, (event_time, feature_time, recorded_at, valid_from, valid_to)
    )
    system_cutoff = None
    if system_as_of is not None:
        value, aware = _parse(system_as_of, "system_as_of")
        if awareness and aware not in awareness:
            raise ValueError("system_as_of timezone convention must match the input")
        system_cutoff = value.replace(tzinfo=timezone.utc) if not aware else value.astimezone(timezone.utc)
    index = {}
    offset = len(event_records)
    for local_index, feature in enumerate(feature_records):
        feature_index = offset + local_index
        if feature_time not in feature:
            raise ValueError(f"feature missing {feature_time}")
        available = parsed[feature_index, feature_time]
        index.setdefault(str(feature[key]), []).append((available, str(feature.get("version", "")), feature_index, feature))
    for values in index.values():
        values.sort(key=lambda item: (item[0], item[1], item[2]))
    result = []
    for event_index, event in enumerate(event_records):
        if event_time not in event:
            raise ValueError(f"event missing {event_time}")
        cutoff = parsed[event_index, event_time]
        candidates = index.get(str(event[key]), [])
        upper = bisect_right(candidates, (cutoff, chr(0x10ffff), float("inf"), {}))
        chosen = None
        for available, _, feature_index, feature in reversed(candidates[:upper]):
            known_at = parsed.get((feature_index, recorded_at), available)
            if known_at > (system_cutoff or cutoff):
                continue
            starts, ends = parsed.get((feature_index, valid_from)), parsed.get((feature_index, valid_to))
            if (starts is not None and cutoff < starts) or (ends is not None and cutoff >= ends):
                continue
            chosen = feature
            break
        row = dict(event)
        for name in feature_names or []:
            if name in row:
                raise ValueError("feature collision: " + name)
            row[name] = chosen.get(name) if chosen else None
        row["_feature_available_at"] = chosen[feature_time] if chosen else None
        row["_feature_version"] = chosen.get("version") if chosen else None
        result.append(row)
    return result
