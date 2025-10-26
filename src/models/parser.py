import re
from dataclasses import dataclass
from typing import List, Set
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

@dataclass
class CarModel:
    name: str
    count: int
    code: str

class ModelParser:
    def __init__(self, driver: WebDriver, previous_models: Set[str]):
        self.driver = driver
        self.previous_models = previous_models

    def parse_models_from_url(self, url: str) -> List[CarModel]:
        models = []
        codes = url.split("/i/s%7C")[1].split("/")[0].split(",")[1:]
        
        for code in codes:
            try:
                model = self._parse_single_model(code)
                if model and model.count > 0 and model.name not in self.previous_models:
                    models.append(model)
            except Exception:
                continue
                
        return models

    def _parse_single_model(self, code: str) -> CarModel:
        count_element = self.driver.find_element(By.CSS_SELECTOR, 
            f"label.fp-model--{code} span.resultcount").get_attribute("innerText")
        name_element = self.driver.find_element(By.CSS_SELECTOR, 
            f"label.fp-model--{code} p.needsclick").get_attribute("innerText")
        
        count = int(count_element.replace("(", "").replace(")", "").strip())
        name = re.sub(r"\s*\(\d+\)\s*$", "", name_element.strip())
        
        return CarModel(name=name, count=count, code=code)