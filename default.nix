# This file defines the Python environment in which Aas runs in production.
let
  sources = import ./nix/sources.nix {};
  pkgs = import sources.nixpkgs {};

  aas-deps = import ./aas.nix { development = false; };

in pkgs.python38.withPackages aas-deps
