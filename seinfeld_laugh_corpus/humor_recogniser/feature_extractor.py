import logging
import logging.config
import types

from humor_recogniser import features as features
from .screenplay import Line, Laugh


class FeatureExtractor:
    """
    A feature extractor for a Seinfeld line.
    The input is this line, the previous 3 lines and next 3 lines.
    """

    def __init__(self, context_window=7):
        """

        :param line: a Line namedtuple.
        :param context: the line's context, i.e an array of which the center is the line and the sides are the preceding
                        /prefixing lines.
        """
        self.context_window = context_window
        logging.config.fileConfig(__file__.rsplit("\\", 1)[0] + '/feature_extractor_logger.conf')
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.DEBUG)

        self.features = {}  # feature's name, extracting function
        # TODO split features to different modules (e.g. 'timing_features', 'semantic_features')
        # TODO and provide switches in the constructor to turn off certain type of features.
        logger.info("The features that I will be extracting:")
        for feature in dir(features):
            if not feature.startswith('_') and isinstance(getattr(features, feature), types.FunctionType):
                logger.info(feature)
                self.features[feature] = getattr(features, feature)

    def extract_features(self, line, context):
        """
        :param line: A line from the screenplay.
        :param context: A list of the before/after lines, while this line is at its center. I haven't yet decided on
                        the size of the window.
        :return: The features formatted as a python dictionary
        """
        extracted = {}
        for function_name, extraction_func in self.features.items():
            for feature_name, value in extraction_func(line, context):
                extracted[feature_name] = value
        return extracted

    def yield_features(self, screenplay):
        """
        (A generator.)
        :param screenplay: A list of Line & Laugh objects represents a full episode's screenplay.
        :return: a tuple (x [features as python dict], y ['funny' or 'not_funny'])
        """
        for i, line in enumerate(screenplay):
            if isinstance(screenplay[i], Line):
                features = self.extract_features(line, self.get_context(screenplay, i))
                if isinstance(screenplay[i+1], Laugh):
                    y = 'funny'
                else:
                    y = 'not_funny'
                yield features, y

    def get_context(self, screenplay, i):
        """
        :param screenplay: a list of Line and Laugh objects.
        :param i: the line's index.
        :return: A list of the lines that come BEFORE the i'th line.
        """
        context = []
        k = self.context_window
        while k >= 0:
            if isinstance(screenplay[i-k], Line) and i-k > 0:
                context.append(screenplay[i-k])
            k -= 1
        return context






if __name__ == '__main__':
    fe = FeatureExtractor()
