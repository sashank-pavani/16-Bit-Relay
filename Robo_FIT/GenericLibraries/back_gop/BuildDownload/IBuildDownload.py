from abc import ABC, abstractmethod


class IBuildDownload(ABC):

    @abstractmethod
    def download_build(self, build_variant: str = None):
        """
        The Function is used to download the build.
         :param build_variant: Name of the build variant, which user provided
            in the Configuration file as 'buildVariant' KEY
        :type build_variant: str
        :return:
        :rtype:
        """
        pass
