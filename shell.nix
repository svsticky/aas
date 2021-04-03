let
  sources = import ./nix/sources.nix {};
  pkgs = import sources.nixpkgs {};

  aas-deps = import ./aas.nix { development = true; };

in
  pkgs.mkShell {
    name = "aas-devenv";
    buildInputs = [
      (pkgs.python37.withPackages aas-deps)
      pkgs.niv
      pkgs.ngrok
    ];
  }
