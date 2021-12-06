# This file defines the Python environment in which Aas runs in production.
let
  sources = import ./nix/sources.nix {};
  pkgs = import sources.nixpkgs {};
  lib = pkgs.lib;


  python = pkgs.python39;

  aas = pkgs.callPackage ./aas.nix { inherit lib python; };

  pythonEnv = pkgs.python39.withPackages (ps: [
    aas
    ps.gunicorn
  ]);

in
{
  inherit pythonEnv;
}
