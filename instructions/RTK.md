# RTK guidance

Use `rtk` as the shell proxy when it is installed:

```text
rtk git status
rtk pytest -q
rtk npm test
```

If `rtk` is not installed or not on `PATH`, report that fact and use the normal platform shell command. Never hardcode another person's absolute executable path.
