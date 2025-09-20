import pymui

def test_vec2():
    vec = pymui.Vec2(5, 7)
    assert vec.x == 5
    assert vec.y == 7

def test_rect():
    rect = pymui.Rect(5, 7, 10, 20)
    assert rect.x == 5
    assert rect.y == 7
    assert rect.w == 10
    assert rect.h == 20

