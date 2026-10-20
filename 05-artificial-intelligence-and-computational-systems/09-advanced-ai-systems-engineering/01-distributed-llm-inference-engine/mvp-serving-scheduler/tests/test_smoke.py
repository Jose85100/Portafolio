from src.simulator import Request, simulate

def test_one_request():
    assert len(simulate([Request(0,0,4,2)],'serial').completions) == 1
