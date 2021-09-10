import abc
from logging import Logger
from typing import Optional, List, Dict, Union, Callable

from slither.core.compilation_unit import SlitherCompilationUnit
from slither.utils.colors import green, yellow, red
from slither.utils.comparable_enum import ComparableEnum
from slither.utils.output import Output, SupportedOutput


class IncorrectCheckInitialization(Exception):
    pass


class CheckClassification(ComparableEnum):
    HIGH = 0
    MEDIUM = 1
    LOW = 2
    INFORMATIONAL = 3
    UNIMPLEMENTED = 999


classification_colors: Dict[CheckClassification, Callable[[str], str]] = {
    CheckClassification.INFORMATIONAL: green,
    CheckClassification.LOW: yellow,
    CheckClassification.MEDIUM: yellow,
    CheckClassification.HIGH: red,
}

classification_txt = {
    CheckClassification.INFORMATIONAL: "Informational",
    CheckClassification.LOW: "Low",
    CheckClassification.MEDIUM: "Medium",
    CheckClassification.HIGH: "High",
}


class AbstractCheck(metaclass=abc.ABCMeta):
    ARGUMENT = ""
    HELP = ""
    IMPACT: CheckClassification = CheckClassification.UNIMPLEMENTED

    WIKI = ""

    WIKI_TITLE = ""
    WIKI_DESCRIPTION = ""
    WIKI_EXPLOIT_SCENARIO = ""
    WIKI_RECOMMENDATION = ""

    def __init__(self, logger: Logger, compilation_unit: SlitherCompilationUnit) -> None:
        self.logger = logger
        self.compilation_unit: SlitherCompilationUnit = compilation_unit

        if not self.ARGUMENT:
            raise IncorrectCheckInitialization(
                "NAME is not initialized {}".format(self.__class__.__name__)
            )

        if not self.HELP:
            raise IncorrectCheckInitialization(
                "HELP is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI:
            raise IncorrectCheckInitialization(
                "WIKI is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI_TITLE:
            raise IncorrectCheckInitialization(
                "WIKI_TITLE is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI_DESCRIPTION:
            raise IncorrectCheckInitialization(
                "WIKI_DESCRIPTION is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI_EXPLOIT_SCENARIO and self.IMPACT not in [
            CheckClassification.INFORMATIONAL
        ]:
            raise IncorrectCheckInitialization(
                "WIKI_EXPLOIT_SCENARIO is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI_RECOMMENDATION:
            raise IncorrectCheckInitialization(
                "WIKI_RECOMMENDATION is not initialized {}".format(self.__class__.__name__)
            )

        if self.IMPACT not in [
            CheckClassification.LOW,
            CheckClassification.MEDIUM,
            CheckClassification.HIGH,
            CheckClassification.INFORMATIONAL,
        ]:
            raise IncorrectCheckInitialization(
                "IMPACT is not initialized {}".format(self.__class__.__name__)
            )

    @abc.abstractmethod
    def _check(self) -> List[Output]:
        """TODO Documentation"""
        return []

    def check(self) -> List[Dict]:
        all_outputs = self._check()
        # Keep only dictionaries
        all_results = [r.data for r in all_outputs]
        if all_results:
            if self.logger:
                info = "\n"
                for result in all_results:
                    info += result["description"]
                info += "Reference: {}".format(self.WIKI)
                self._log(info)
        return all_results

    def generate_result(
        self,
        info: Union[str, List[Union[str, SupportedOutput]]],
        additional_fields: Optional[Dict] = None,
    ) -> Output:
        output = Output(
            info, additional_fields, markdown_root=self.compilation_unit.core.markdown_root
        )

        output.data["check"] = self.ARGUMENT

        return output

    def _log(self, info: str) -> None:
        if self.logger:
            self.logger.info(self.color(info))

    @property
    def color(self) -> Callable[[str], str]:
        return classification_colors[self.IMPACT]