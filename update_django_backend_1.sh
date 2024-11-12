TARGET_DIR="django_backend"
SRC_DIR="truong-dev"
rm -rf "$TARGET_DIR"

mkdir "$TARGET_DIR"

git archive "$SRC_DIR" | tar -x -C ./"$TARGET_DIR"

git add "$TARGET_DIR"
git commit -m "update django_backed from main branch to '$TARGET_DIR'"
git push