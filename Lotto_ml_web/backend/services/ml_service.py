import numpy as np
import pandas as pd
import joblib
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split

from config import MODEL_PATH
from services.data_service import get_all_results_df


def extract_features(df: pd.DataFrame, idx: int) -> List[float]:
    """Extract 79 features for ML model."""
    features: List[float] = []

    # 1. Previous 5 draws (30 features)
    for i in range(1, 6):
        if idx - i >= 0:
            prev = df.iloc[idx - i]
            for j in range(1, 7):
                features.append(float(prev[f'num{j}']))
        else:
            features.extend([0.0] * 6)

    # 2. Previous draw odd/even ratio (1 feature)
    if idx > 0:
        prev = df.iloc[idx - 1]
        nums = [prev[f'num{j}'] for j in range(1, 7)]
        odd_ratio = sum(1 for n in nums if n % 2 == 1) / 6
    else:
        odd_ratio = 0.5
    features.append(odd_ratio)

    # 3. Previous draw high/low ratio (1 feature) - threshold: 23
    if idx > 0:
        high_ratio = sum(1 for n in nums if n > 23) / 6
    else:
        high_ratio = 0.5
    features.append(high_ratio)

    # 4. Mean and std of previous draw (2 features)
    if idx > 0:
        features.append(float(np.mean(nums)))
        features.append(float(np.std(nums)))
    else:
        features.extend([23.0, 10.0])

    # 5. Each number's frequency in recent 100 draws (45 features)
    recent = df.iloc[max(0, idx - 100):idx]
    for num in range(1, 46):
        if len(recent) > 0:
            count = sum(
                (recent[f'num{j}'] == num).sum()
                for j in range(1, 7)
            )
            features.append(count / len(recent))
        else:
            features.append(0.0)

    return features  # Total: 79 features


def prepare_training_data(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare training data (X, y) from dataframe."""
    X: List[List[float]] = []
    y: List[List[int]] = []

    # Start from index 5 (need 5 previous draws)
    for idx in range(5, len(df)):
        features = extract_features(df, idx)
        targets = [df.iloc[idx][f'num{j}'] for j in range(1, 7)]
        X.append(features)
        y.append(targets)

    return np.array(X), np.array(y)


def train_models() -> Dict[str, Any]:
    """Train all ML models and save them."""
    MODEL_PATH.mkdir(parents=True, exist_ok=True)

    df = get_all_results_df()
    if len(df) < 10:
        raise ValueError("Not enough data to train models. Please sync data first.")

    X, y = prepare_training_data(df)

    # Train/Test split (80/20) for proper evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler
    joblib.dump(scaler, MODEL_PATH / "scaler.pkl")

    results: Dict[str, Any] = {}

    # Train Random Forest (reduced complexity)
    rf_model = MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=100,
            max_depth=6,  # Reduced from 10
            min_samples_split=10,  # Added to prevent overfitting
            min_samples_leaf=5,  # Added to prevent overfitting
            random_state=42,
            n_jobs=-1
        )
    )
    rf_model.fit(X_train_scaled, y_train)
    joblib.dump(rf_model, MODEL_PATH / "random_forest.pkl")
    rf_train_acc = evaluate_model(rf_model, X_train_scaled, y_train)
    rf_test_acc = evaluate_model(rf_model, X_test_scaled, y_test)
    results["random_forest"] = {
        "train_accuracy": rf_train_acc,
        "test_accuracy": rf_test_acc,
        "trained": True
    }

    # Train Gradient Boosting (reduced complexity)
    gb_model = MultiOutputRegressor(
        GradientBoostingRegressor(
            n_estimators=50,
            max_depth=3,  # Reduced from 5
            min_samples_split=10,  # Added
            min_samples_leaf=5,  # Added
            learning_rate=0.1,
            random_state=42
        )
    )
    gb_model.fit(X_train_scaled, y_train)
    joblib.dump(gb_model, MODEL_PATH / "gradient_boosting.pkl")
    gb_train_acc = evaluate_model(gb_model, X_train_scaled, y_train)
    gb_test_acc = evaluate_model(gb_model, X_test_scaled, y_test)
    results["gradient_boosting"] = {
        "train_accuracy": gb_train_acc,
        "test_accuracy": gb_test_acc,
        "trained": True
    }

    # Train Neural Network (MLP) with regularization
    mlp_model = MultiOutputRegressor(
        MLPRegressor(
            hidden_layer_sizes=(64, 32),  # Reduced from (128, 64, 32)
            activation='relu',
            alpha=0.01,  # L2 regularization
            learning_rate='adaptive',
            learning_rate_init=0.001,
            max_iter=300,  # Reduced from 500
            early_stopping=True,  # Stop when validation score stops improving
            validation_fraction=0.15,
            n_iter_no_change=20,
            random_state=42
        )
    )
    mlp_model.fit(X_train_scaled, y_train)
    joblib.dump(mlp_model, MODEL_PATH / "neural_network.pkl")
    mlp_train_acc = evaluate_model(mlp_model, X_train_scaled, y_train)
    mlp_test_acc = evaluate_model(mlp_model, X_test_scaled, y_test)
    results["neural_network"] = {
        "train_accuracy": mlp_train_acc,
        "test_accuracy": mlp_test_acc,
        "trained": True
    }

    # Save training info
    training_info = {
        "trained_at": datetime.now().isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    }
    joblib.dump(training_info, MODEL_PATH / "training_info.pkl")

    # Save model accuracies for prediction
    model_accuracies = {
        "random_forest": {"train_accuracy": rf_train_acc, "test_accuracy": rf_test_acc},
        "gradient_boosting": {"train_accuracy": gb_train_acc, "test_accuracy": gb_test_acc},
        "neural_network": {"train_accuracy": mlp_train_acc, "test_accuracy": mlp_test_acc}
    }
    joblib.dump(model_accuracies, MODEL_PATH / "model_accuracies.pkl")

    return {
        "models": results,
        "trained_at": training_info["trained_at"],
        "training_samples": training_info["training_samples"],
        "test_samples": training_info["test_samples"]
    }


def evaluate_model(model: Any, X: np.ndarray, y: np.ndarray) -> float:
    """Evaluate model with ±3 accuracy metric."""
    predictions = model.predict(X)
    correct = 0
    total = 0

    for i in range(len(predictions)):
        for j in range(6):
            pred = round(predictions[i][j])
            actual = y[i][j]
            if abs(pred - actual) <= 3:
                correct += 1
            total += 1

    return round(correct / total, 4) if total > 0 else 0.0


def predict_numbers() -> Dict[str, Any]:
    """Generate predictions from all models."""
    if not _models_exist():
        raise ValueError("Models not trained. Please train models first.")

    df = get_all_results_df()
    if len(df) < 5:
        raise ValueError("Not enough data for prediction.")

    # Get latest features
    features = extract_features(df, len(df))

    # Load scaler and scale features
    scaler = joblib.load(MODEL_PATH / "scaler.pkl")
    features_scaled = scaler.transform([features])

    # Load training info and model accuracies
    training_info = joblib.load(MODEL_PATH / "training_info.pkl")
    model_accuracies = joblib.load(MODEL_PATH / "model_accuracies.pkl") if (MODEL_PATH / "model_accuracies.pkl").exists() else {}

    predictions: Dict[str, Any] = {}

    model_names = ["random_forest", "gradient_boosting", "neural_network"]
    for model_name in model_names:
        model = joblib.load(MODEL_PATH / f"{model_name}.pkl")
        raw_pred = model.predict(features_scaled)[0]

        # Post-process predictions
        numbers = _postprocess_prediction(raw_pred)

        # Use saved test accuracy (not re-evaluated on full training data)
        accuracy = model_accuracies.get(model_name, {}).get("test_accuracy", 0.0)

        predictions[model_name] = {
            "numbers": numbers,
            "accuracy": accuracy
        }

    return {
        "predictions": predictions,
        "disclaimer": "로또는 무작위 추첨이므로 예측이 불가능합니다. 이 결과는 참고용입니다.",
        "last_trained": training_info.get("trained_at")
    }


def _postprocess_prediction(raw_pred: np.ndarray) -> List[int]:
    """Post-process raw prediction to valid lotto numbers."""
    numbers = []

    for pred in raw_pred:
        num = max(1, min(45, round(pred)))
        numbers.append(num)

    # Remove duplicates and fill with random numbers
    numbers = list(set(numbers))
    while len(numbers) < 6:
        new_num = random.randint(1, 45)
        if new_num not in numbers:
            numbers.append(new_num)

    return sorted(numbers[:6])


def _models_exist() -> bool:
    """Check if all model files exist."""
    required_files = [
        "scaler.pkl",
        "random_forest.pkl",
        "gradient_boosting.pkl",
        "neural_network.pkl",
        "training_info.pkl"
    ]
    return all((MODEL_PATH / f).exists() for f in required_files)


def get_model_status() -> Dict[str, Any]:
    """Get current model status."""
    if not _models_exist():
        return {
            "trained": False,
            "last_trained": None,
            "models_available": []
        }

    training_info = joblib.load(MODEL_PATH / "training_info.pkl")

    return {
        "trained": True,
        "last_trained": training_info.get("trained_at"),
        "models_available": ["random_forest", "gradient_boosting", "neural_network"]
    }
