from lyapgeo.cli import build_parser

def test_cli_parser():
    args = build_parser().parse_args(['benchmark-logistic','--outdir','tmp','--n-bootstrap','10'])
    assert args.cmd == 'benchmark-logistic'
