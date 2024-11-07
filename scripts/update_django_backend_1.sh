TARGET_DIR="django_backend"

rm -rf "$TARGET_DIR"

mkdir "$TARGET_DIR"

git archive main | tar -x -C ./"$TARGET_DIR"

git add "$TARGET_DIR"
git commit -m "update django_backed from main branch to '$TARGET_DIR'"
git push