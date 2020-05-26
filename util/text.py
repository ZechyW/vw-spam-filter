import re


def process_text(text):
    """
    General-purpose text pre-processing.

    :param text:
    :return:
    """
    if text is None:
        return ""

    text = text.casefold()

    # Remove 1 and 2 character alphabetic words
    # (Uncomment if necessary)
    # text = re.sub(r"\b[a-z]{1,2}\b", "", text)

    # Split non alphabetic chars out into separate tokens
    text = re.sub(r"([^a-z ]+)", r" \1 ", text)

    # Convert all extraneous whitespace to single spaces
    text = re.sub(r"\s+", " ", text)

    return text


def to_vw_format(feature_spaces, label=None):
    """
    Provide a mapping of feature namespaces -> feature strings with an optional
    label for a single example, and this function will return the data in the format
    expected by Vowpal Wabbit.

    Feature strings are space-separated lists of features, where each feature is in
    the format <feature name>[:<feature value>].  If `feature_value` is omitted,
    it is taken to be 1.  A basic list of tokens therefore corresponds to a set of
    features named after the tokens, each with value 1.

    This function ensures that the VW special characters "|" and ":" are not present
    in any feature string, but does no further pre-processing.

    :param feature_spaces:
    :param label:
    :return:
    """
    # Build the components of the VW-formatted line as a string, then join them at
    # the end
    vw = []

    if label is not None:
        vw.append(f"{label}")

    for name, features in feature_spaces.items():
        features = features.replace("|", "").replace(":", "")
        features = re.sub(r"\s+", " ", features)
        vw.append(f"|{name} {features}")

    return " ".join(vw)
