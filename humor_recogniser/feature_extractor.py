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

    def __init__(self):
        """

        :param line: a Line namedtuple.
        :param context: the line's context, i.e an array of which the center is the line and the sides are the preceding
                        /prefixing lines.
        """
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
        extracted = {}
        assert line == context[len(context)/2]
        for feature_name, feature_extraction_method in self.features.items():
            feature.extract(line, context)


if __name__ == '__main__':
    fe = FeatureExtractor()
