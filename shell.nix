let
  sources = import ./nix/sources.nix {};
  pkgs = import sources.nixpkgs {};
  pkgs-unfree = import sources.nixpkgs {
    config = { allowUnfree = true; };
  };

  aas-deps = import ./aas.nix { development = true; };

in
  pkgs.mkShell {
    name = "aas-devenv";
    buildInputs = [
      (pkgs.python38.withPackages aas-deps)
      pkgs.niv
      pkgs-unfree.ngrok
    ];
  }
