{
  description = "Jyogi Navi development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Node.js
            nodejs_20
            pnpm

            # Python
            python313
            uv

            # Infrastructure
            terraform
            tflint

            # Development tools
            lefthook
            gh
          ];

          shellHook = ''
            echo "🚀 Jyogi Navi development environment loaded!"
            echo ""
            echo "Available tools:"
            echo "  - Node.js $(node --version)"
            echo "  - pnpm $(pnpm --version)"
            echo "  - Python $(python --version | cut -d' ' -f2)"
            echo "  - uv $(uv --version | cut -d' ' -f2)"
            echo "  - terraform $(terraform --version | head -n1 | cut -d'v' -f2)"
            echo "  - tflint $(tflint --version | head -n1 | awk '{print $NF}')"
            echo "  - lefthook $(lefthook version)"
            echo "  - gh $(gh --version | head -n1 | cut -d' ' -f3)"
            echo ""
          '';
        };
      }
    );
}
