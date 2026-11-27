from app.analysers.base import Analyser
from app.analysers.bandit import BanditAnalyser

# A new analyser is one module plus one entry here (NFR-05).
ANALYSERS: dict[str, Analyser] = {analyser.name: analyser for analyser in (BanditAnalyser(),)}
SUPPORTED_ANALYSERS = tuple(ANALYSERS)
