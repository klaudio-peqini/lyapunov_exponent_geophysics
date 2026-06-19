import pandas as pd
from lyapgeo.io import read_series

def test_read_excel_series(tmp_path):
    path = tmp_path / "example.xlsx"
    pd.DataFrame({"Age (kyr)": [0.0, 0.001], "RPI": [0.79, 0.89]}).to_excel(path, index=False)
    x = read_series(path, input_format="excel", sheet=0, column="RPI")
    assert x.tolist() == [0.79, 0.89]
