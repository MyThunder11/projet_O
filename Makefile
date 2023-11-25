
default: pytest

streamlit:
	@streamlit run app.py

slides:
	@jupyter nbconvert viz.ipynb --to slides --post serve \
	--no-prompt \
	--TagRemovePreprocessor.remove_input_tags=remove_input \
	--TagRemovePreprocessor.remove_all_outputs_tags=remove_output
