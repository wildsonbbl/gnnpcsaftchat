script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
version_file="$script_dir/app/_version.py"
version_number="$(sed -nE 's/.*"([0-9]+\.[0-9]+\.[0-9]+)".*/\1/p' "$version_file" | head -n 1)"
skip_upload=false
rtcompat=false

if [ "${1:-}" = "--skip-upload" ]; then
	skip_upload=true
fi
if [ "${1:-}" = "--rtcompat" ] || [ "${2:-}" = "--rtcompat" ]; then
	rtcompat=true
fi

set -euo pipefail

if [ -z "$version_number" ]; then
	echo "Could not find version in $version_file" >&2
	exit 1
fi

version="v$version_number"
arch="$(dpkg --print-architecture)"
binary_name="gnnpcsaftchat"
package_name="$binary_name"
if [ "$rtcompat" = true ]; then
	package_name="gnnpcsaftchat-rtcompat"
fi
deb_file="${package_name}_${version_number}_${arch}.deb"
app_dir="$script_dir"

if [ -n "${PYTHONPATH:-}" ]; then
	export PYTHONPATH="$app_dir:$PYTHONPATH"
else
	export PYTHONPATH="$app_dir"
fi

## create package
uv pip install -r requirements.txt
if [ "$rtcompat" = true ]; then
	uv pip install 'polars[rtcompat]'
fi
uv pip install pywebview[qt]
uv run python manage.py collectstatic --no-input
uv run python manage.py migrate --no-input
uv run pyinstaller --distpath ./app_pkg/dist --workpath ./app_pkg/build --noconfirm --clean ./gnnpcsaftchat.spec

dist_dir="$script_dir/app_pkg/dist/gnnpcsaftchat"
pkg_root="$script_dir/app_pkg/dist/deb_pkg"
icon_src="$script_dir/chat/static/images/icons/ios/512.png"

rm -rf "$pkg_root"
mkdir -p \
	"$pkg_root/DEBIAN" \
	"$pkg_root/opt/$package_name" \
	"$pkg_root/usr/bin" \
	"$pkg_root/usr/share/applications" \
	"$pkg_root/usr/share/icons/hicolor/512x512/apps"

cp -a "$dist_dir/." "$pkg_root/opt/$package_name/"
ln -sf "/opt/$package_name/$binary_name" "$pkg_root/usr/bin/$package_name"
cp "$icon_src" "$pkg_root/usr/share/icons/hicolor/512x512/apps/$package_name.png"

cat > "$pkg_root/usr/share/applications/$package_name.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$package_name
Comment=GNNPCSAFT Chat desktop application
Exec=$package_name
Icon=$package_name
Terminal=false
Categories=Science;Education;
EOF

chmod 644 \
	"$pkg_root/usr/share/icons/hicolor/512x512/apps/$package_name.png" \
	"$pkg_root/usr/share/applications/$package_name.desktop"

installed_size="$(du -sk "$pkg_root" | awk '{print $1}')"

cat > "$pkg_root/DEBIAN/control" <<EOF
Package: $package_name
Version: $version_number
Section: utils
Priority: optional
Architecture: $arch
Maintainer: Wildson B. B. Lima <wil_bbl@hotmail.com>
Homepage: https://github.com/wildsonbbl/gnnpcsaftchat
Installed-Size: $installed_size
Depends:libgl1, libglib2.0-0, libsm6, libxrender1, libxext6, libegl1, libmtdev1, xvfb, libnss3
Description: GNNPCSAFT chat desktop application
 Graph Neural Network + PC-SAFT for thermodynamic modeling.
EOF

dpkg-deb --build "$pkg_root" "$script_dir/app_pkg/dist/$deb_file"

## add artifact to release
if [ "$skip_upload" != true ]; then
	gh release upload "$version" "$script_dir/app_pkg/dist/$deb_file" --clobber
fi