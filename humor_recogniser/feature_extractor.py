import logging
import logging.config

from screenplay import Line
import features

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)


class FeatureExtractor:
    """
    A feature extractor for a Seinfeld line.
    The input is this line, the previous 3 lines and next 3 lines.
    """

    def __init__(self, context_window=5):
        """

        :param line: a Line namedtuple.
        :param context: the line's context, i.e an array of which the center is the line and the sides are the preceding
                        /prefixing lines.
        """
        self.context_window = context_window
        logging.config.fileConfig('feature_extractor_logger.conf')
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.DEBUG)

        self.features = {}  # feature's name, extracting function
        # TODO split features to different modules (e.g. 'timing_features', 'semantic_features')
        # TODO and provide switches in the constructor to turn off certain type of features.
        logger.info("The features that I will be extracting:")
        for feature in dir(features):
            if not feature.startswith('_'):
                logger.info(feature)
                self.features[feature] = getattr(features, feature)
            pass

    def extract_features(self, line, context):
        """
        :param line: A line from the screenplay.
        :param context: A list of the before/after lines, while this line is at its center. I haven't yet decided on
                        the size of the window.
        :return: The features formatted as a python dictionary
        """
        extracted = {}
        assert line == context[len(context)/2]
        for feature_name, extraction_func in self.features.items():
            extracted[feature_name] = extraction_func(line, context)

    def yield_features(self, screenplay):
        """
        (A generator.)
        :param screenplay: A list of Line & Laugh objects represents a full episode's screenplay.
        :return: a tuple (x [features as python dict], y ['funny' or 'not_funny'])
        """
        for i, line in enumerate(screenplay):
            features = self.extract(line, self.get_context(screenplay, i))
            if instanceof(screenplay[i+1], Laugh):
                y = 'funny'
            else:
                y = 'not_funny'
            yield features, y

    def get_context(self, screenplay, i):
        """
        :param screenplay: a list of Line and Laugh objects.
        :param i: the line's index.
        :return: A list of before/after lines of the i'th line.
        """
        context = []
        for k in range(-self.context_window, self.context_window + 1):
            try:
                context.append(screenplay[i+k])
            except IndexError:
                context.append(None)
        return context






if __name__ == '__main__':
    fe = FeatureExtractor()
