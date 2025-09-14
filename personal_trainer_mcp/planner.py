from pydantic import BaseModel, Field

class ComputeMetricsArgs(BaseModel):
    sexo: str
    edad: int
    altura_cm: int
    peso_kg: int

def compute_metrics(args: ComputeMetricsArgs):
    """Computes BMI and BMR (Mifflin–St Jeor)"""
    # BMI = peso / (altura_m^2)
    altura_m = args.altura_cm / 100
    bmi = args.peso_kg / (altura_m * altura_m)

    # BMR (Mifflin-St Jeor)
    if args.sexo.lower() == 'male':
        bmr = (10 * args.peso_kg) + (6.25 * args.altura_cm) - (5 * args.edad) + 5
    else:
        bmr = (10 * args.peso_kg) + (6.25 * args.altura_cm) - (5 * args.edad) - 161

    return {
        "bmi": round(bmi, 2),
        "bmr": round(bmr, 2)
    }

class RecommendExercisesArgs(BaseModel):
    objetivo: str
    deporte: str
    limite: int

def recommend_exercises(args: RecommendExercisesArgs):
    """Recommendations by goal/sport"""
    # Implementation will be added later
    return {"message": "recommend_exercises tool called"}

class BuildRoutineToolArgs(BaseModel):
    objetivo: str
    dias_por_semana: int
    minutos_por_sesion: int
    experiencia: str

def build_routine_tool(args: BuildRoutineToolArgs):
    """Weekly routine (sets/reps/timing)"""
    # Implementation will be added later
    return {"message": "build_routine_tool tool called"}

class RecommendByMetricsToolArgs(BaseModel):
    sexo: str
    edad: int
    altura_cm: int
    peso_kg: int
    objetivo: str
    limite: int

def recommend_by_metrics_tool(args: RecommendByMetricsToolArgs):
    """Recommendations using metrics + goal"""
    # Implementation will be added later
    return {"message": "recommend_by_metrics_tool tool called"}