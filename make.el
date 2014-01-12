(require 'org)
(require 'org-exp)
(require 'ob)
(require 'ob-tangle)

(with-current-buffer (find-file "./README.org")
  (org-babel-tangle))
