from core.base_exercise import BaseExercise


class PushUpDetector(BaseExercise):
    DOWN_THRESHOLD = 90
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    LEFT_HIP = 23
    LEFT_ANKLE = 27
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    RIGHT_HIP = 24
    RIGHT_ANKLE = 28

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        sides = (
            (self.LEFT_SHOULDER, self.LEFT_ELBOW, self.LEFT_WRIST, self.LEFT_HIP, self.LEFT_ANKLE),
            (self.RIGHT_SHOULDER, self.RIGHT_ELBOW, self.RIGHT_WRIST, self.RIGHT_HIP, self.RIGHT_ANKLE),
        )
        indices = max(
            sides,
            key=lambda side: sum(landmarks[index].visibility for index in side),
        )
        shoulder_idx, elbow_idx, wrist_idx, hip_idx, ankle_idx = indices

        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        hip_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )
        key_landmarks_visible = all(
            landmarks[index].visibility >= self.MIN_VISIBILITY
            for index in indices
        )

        if key_landmarks_visible:
            if elbow_angle <= self.DOWN_THRESHOLD:
                self.stage = "down"
            elif elbow_angle >= self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

        body_alignment = "GOOD" if hip_angle >= 160 else "MISALIGNED"
        hip_status = "NEUTRAL" if hip_angle >= 160 else "OUT OF LINE"

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "body_alignment": body_alignment,
            "hip_status": hip_status,
        }
    