from lyapgeo.io import read_radon_eye, read_series


def test_read_radon_eye(tmp_path):
    p = tmp_path / "radon.txt"
    p.write_text(
        "FTLAB RADON DATA FILE\n"
        "MODEL NAME:\tRadon Eye Plus\n"
        "Unit:\tBq/m3\n"
        "1)\t2024-02-08 17:49:17\t 21\t20.5°C\t60%\n"
        "2)\t2024-02-08 18:49:17\t 31\t20.5°C\t61%\n",
        encoding="utf-8",
    )
    df = read_radon_eye(p)
    assert df["radon_bq_m3"].tolist() == [21.0, 31.0]
    assert df["temperature_c"].tolist() == [20.5, 20.5]
    assert df["humidity_percent"].tolist() == [60.0, 61.0]
    assert read_series(p, input_format="radon-eye", column="radon").tolist() == [21.0, 31.0]
