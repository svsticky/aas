{
  lib,
  python,
}:
python.pkgs.buildPythonPackage {
  pname = "aas";
  version = "1.0";

  # Include all Python files + their containing directories
  src = lib.cleanSourceWith {
    src = ./.;
    filter = path: type:
        type == "directory" ||
        lib.hasSuffix ".py" path;
  };

  propagatedBuildInputs = with python.pkgs; [
    flask
    flask-restful
    python-dotenv
    requests
  ];
}
