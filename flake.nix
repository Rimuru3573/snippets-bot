{
  description = "snippets bot flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      # Разрешаем проприетарщину (Chrome) внутри этого флейка
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          (pkgs.python3.withPackages (python-pkgs: [
            python-pkgs.pip
          ]))
        ];

        shellHook = ''
          echo "Окружение готово."
        '';
      };
    };
}
