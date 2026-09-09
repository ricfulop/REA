.PHONY: all clean
all:
	python3 build_taxonomy.py
	python3 figures/build_figures.py
	cd iclr2027 && latexmk -pdf -interaction=nonstopmode -halt-on-error rea.tex
clean:
	cd iclr2027 && latexmk -c rea.tex
