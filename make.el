
;(add-to-list 'load-path (expand-file-name "~/src/org/lisp/"))
;(add-to-list 'load-path (expand-file-name "~/src/org/contrib/lisp/" t))
(require 'org)
(require 'org-exp)
(require 'ob)
(require 'ob-tangle)

(with-current-buffer (find-file "./README.org")
  (org-babel-tangle))
