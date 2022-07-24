#!/bin/sh

echo -e "#!/bin/sh\npytest cardvisionpy/tests/*" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
