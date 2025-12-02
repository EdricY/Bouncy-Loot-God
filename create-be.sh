git pull
oldtag=$(git describe --tags --match="be-*" --abbrev=0)
echo "oldtag: $oldtag"
num=${oldtag#*-}
num=$((10#$num + 1))
newtag="be-$(printf "%02d" "$num")"
echo "newtag: $newtag"
git tag $newtag
git push origin $newtag

python zip-it.py
gh release edit $oldtag --tag $newtag
gh release upload $newtag --clobber ./dist/borderlands2.apworld ./dist/BouncyLootGod.sdkmod
