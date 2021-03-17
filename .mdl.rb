# Enable all rules by default
all

# Allow any line length
# https://github.com/markdownlint/markdownlint/blob/master/docs/RULES.md#md013---line-length
exclude_rule 'MD013'

# Allow ordered lists
# https://github.com/markdownlint/markdownlint/blob/master/docs/RULES.md#md029---ordered-list-item-prefix
rule 'MD029', :style => 'ordered'

# Allow nesting to permit similar heads as in CHANGELOG.md
# https://github.com/markdownlint/markdownlint/blob/master/docs/RULES.md#md024---multiple-headers-with-the-same-content
rule 'MD024', :allow_different_nesting => true

# Use 4-space indents since mkdocs seems to prefer this
# https://github.com/markdownlint/markdownlint/blob/master/docs/RULES.md#md007---unordered-list-indentation
rule 'MD007', :indent => 4