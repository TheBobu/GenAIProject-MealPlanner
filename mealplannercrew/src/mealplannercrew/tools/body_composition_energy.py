import json
from crewai.tools import tool

@tool("personal_health_calculator")
def health_calculator(
    weight_kg: float, 
    height_cm: float, 
    age: int, 
    gender: str, 
    activity_level: float = 1.2
) -> str:
    """
    Calculates health metrics including BMI and caloric needs based on user stats.
    
    Args:
        weight_kg: Weight in kilograms.
        height_cm: Height in centimeters.
        age: Age in years.
        gender: Must be 'male' or 'female'.
        activity_level: Activity factor (1.2: Sedentary, 1.375: Light, 1.55: Moderate, 1.725: Active).
    """
    # bmi
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    # bmr
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    # tdee
    maintenance = round(bmr * activity_level)

    # result
    result = {
        "bmi": bmi,
        "maintenance_kcal": maintenance,
        "weight_loss_kcal": maintenance - 500,
        "weight_gain_kcal": maintenance + 500
    }

    return json.dumps(result)