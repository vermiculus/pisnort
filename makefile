tangle:
	emacs --batch --eval "(load \"$(CURDIR)/make.el\")" 2>&1
install:
	echo "cd $(CURDIR) && ./main.py &" >> /etc/rc.local
