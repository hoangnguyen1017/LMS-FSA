TARGET_DIR="django_backend"

rm -rf "$TARGET_DIR"

mkdir "$TARGET_DIR"

git archive main | tar -x -C ./"$TARGET_DIR"