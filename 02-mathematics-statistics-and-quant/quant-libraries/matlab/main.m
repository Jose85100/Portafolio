% MATLAB / Octave: producto elemento a elemento y suma matricial.
pd = [0.02; 0.05; 0.10];
lgd = [0.4; 0.6; 0.3];
ead = [1000; 2000; 500];
assert(isequal(size(pd), size(lgd)) && isequal(size(pd), size(ead)));
assert(all(isfinite(pd)) && all(isfinite(lgd)) && all(isfinite(ead)));
assert(all(pd >= 0 & pd <= 1));
assert(all(lgd >= 0 & lgd <= 1));
assert(all(ead >= 0));
expected_loss = sum(pd .* lgd .* ead);
assert(abs(expected_loss - 83.0) < 1e-10);
fprintf('EL=%.10f\n', expected_loss);
