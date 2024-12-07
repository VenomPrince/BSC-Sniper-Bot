{
  description = "Python environment for BSC Sniper Bot";
  deps = [
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.nodejs
    pkgs.nodePackages.npm
  ];
}
