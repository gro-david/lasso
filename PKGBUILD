# Maintainer: David Gro <your.email@example.com>
pkgname=fuse-launcher
pkgver=r67.c183cb4
pkgrel=1
pkgdesc="A program called fuse launcher"
arch=('x86_64')
url="https://github.com/gro-david/fuse"
license=('MIT')
depends=('python')
source=("git+https://github.com/gro-david/fuse.git")
sha256sums=('SKIP')

pkgver() {
    cd "$srcdir/fuse"
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

build() {
    cd "$srcdir/fuse"
}

package() {
    cd "$srcdir/fuse"
    install -d "$pkgdir/usr/share/$pkgname"
    cp -r {modules,res,fuse.py,start.py} "$pkgdir/usr/share/$pkgname"

    # Create binary files
    install -Dm755 /dev/stdin "$pkgdir/usr/bin/fuse-start" <<EOF
#!/bin/bash
python /usr/share/$pkgname/start.py "\$@"
EOF

    install -Dm755 /dev/stdin "$pkgdir/usr/bin/fuse-network" <<EOF
#!/bin/bash
python /usr/share/$pkgname/modules/network.py "\$@"
EOF

    install -Dm755 /dev/stdin "$pkgdir/usr/bin/fuse-bluetooth" <<EOF
#!/bin/bash
python /usr/share/$pkgname/modules/bluetooth.py "\$@"
EOF
}
