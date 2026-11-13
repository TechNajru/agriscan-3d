import io

from tests.synth import encode, make_scene


def post(client, img_bytes, name="a.jpg", mime="image/jpeg", **data):
    return client.post("/api/analyze", files={"image": (name, io.BytesIO(img_bytes), mime)}, data=data)


def test_health_and_config(client):
    assert client.get("/api/health").json()["status"] == "ok"
    cfg = client.get("/api/config").json()
    assert cfg["fruits"][0]["id"] == "apple" and cfg["experimental_defects"] is True


def test_analyze_and_fetch_everything(client):
    r = post(client, encode(make_scene("bruised", with_card=True)), reference_width_mm="85.6")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["grade"] == "B" and body["size"]["basis"] == "absolute"
    assert client.get(body["original_url"]).status_code == 200
    assert client.get(body["annotated_url"]).headers["content-type"] == "image/jpeg"
    got = client.get(f"/api/analysis/{body['id']}").json()
    assert got["id"] == body["id"]
    for lang in ("en", "hi"):
        pdf = client.get(f"/api/analysis/{body['id']}/report.pdf", params={"lang": lang})
        assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF") and len(pdf.content) > 5000


def test_png_and_webp_accepted(client):
    for ext, mime in ((".png", "image/png"), (".webp", "image/webp")):
        r = post(client, encode(make_scene("good"), ext), name="x" + ext, mime=mime)
        assert r.status_code == 200, (ext, r.text)


def test_invalid_files_rejected(client):
    r = post(client, b"not an image at all", name="x.jpg")
    assert r.status_code == 400 and r.json()["detail"]["code"] == "invalid_file"
    r = post(client, b"%PDF-1.4 fake", name="x.jpg", mime="image/jpeg")
    assert r.status_code == 400
    r = post(client, b"\xff\xd8\xff" + b"garbage" * 100, name="x.jpg")
    assert r.status_code == 400


def test_too_large_rejected(client):
    r = post(client, b"\xff\xd8\xff" + b"0" * (10 * 1024 * 1024 + 10))
    assert r.status_code == 413 and r.json()["detail"]["code"] == "file_too_large"


def test_blurry_photo_returns_translatable_code(client):
    r = post(client, encode(make_scene("blurry")))
    assert r.status_code == 422 and r.json()["detail"]["code"] == "too_blurry"


def test_unknown_fruit_and_missing_analysis(client):
    assert post(client, encode(make_scene("good")), fruit="mango").status_code == 400
    assert client.get("/api/analysis/doesnotexist").status_code == 404


def test_history_keeps_only_the_newest_n_and_delete_works(client):
    ids = [post(client, encode(make_scene("good", seed=s))).json()["id"] for s in range(5)]
    items = client.get("/api/history").json()["items"]
    assert len(items) == 3 and items[0]["id"] == ids[-1]
    assert client.get(f"/api/analysis/{ids[0]}").status_code == 404           # pruned
    assert client.delete(f"/api/analysis/{ids[-1]}").status_code == 204
    assert client.get(f"/api/analysis/{ids[-1]}").status_code == 404
