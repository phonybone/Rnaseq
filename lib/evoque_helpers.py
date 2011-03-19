from evoque.quoted.quoted_no_more import quoted_no_more

class evoque_no_quote(quoted_no_more):
    def _quote(cls, s):
	return s

    _quote = classmethod(_quote)
