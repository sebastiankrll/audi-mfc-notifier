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
        m = re.search(r"/i/s(?:%7C|\|)([^/]+)", url)
        if not m:
            return self.parse_all_models_from_page()
        
        codes_str = m.group(1)
        raw_codes = [c.strip() for c in codes_str.split(",") if c.strip()]
        codes = [c for c in raw_codes if not c.isdigit()]

        models: List[CarModel] = []
        
        for code in codes:
            model = self._parse_single_model(code)
            if model and model.count > 0 and model.name not in self.previous_models:
                models.append(model)
                
        return models
    
    def parse_all_models_from_page(self) -> List[CarModel]:
        models: List[CarModel] = []
        labels = self.driver.find_elements(By.CSS_SELECTOR, "label[class^='fp-model--']")

        for label in labels:
            class_attr = label.get_attribute("class") or ""
            m = re.search(r"fp-model--([A-Za-z0-9_-]+)", class_attr)
            if not m:
                continue
            code = m.group(1)

            count_elem = label.find_element(By.CSS_SELECTOR, "span.resultcount")
            name_elem = label.find_element(By.CSS_SELECTOR, "p.needsclick")

            count_text = count_elem.get_attribute("innerText") or ""
            name_text = name_elem.get_attribute("innerText") or ""

            count = int(re.sub(r"[^\d]", "", count_text)) if re.search(r"\d", count_text) else 0
            name = re.sub(r"\s*\(\d+\)\s*$", "", name_text.strip())

            if count > 0 and name not in self.previous_models:
                models.append(CarModel(name=name, count=count, code=code))

        return models

    def _parse_single_model(self, code: str) -> CarModel:
        count_elem = self.driver.find_element(By.CSS_SELECTOR, f"label.fp-model--{code} span.resultcount")
        name_elem = self.driver.find_element(By.CSS_SELECTOR, f"label.fp-model--{code} p.needsclick")
        
        count_text = count_elem.get_attribute("innerText") or ""
        name_text = name_elem.get_attribute("innerText") or ""
        
        count = int(re.sub(r"[^\d]", "", count_text)) if re.search(r"\d", count_text) else 0
        name = re.sub(r"\s*\(\d+\)\s*$", "", name_text.strip())
        
        return CarModel(name=name, count=count, code=code)