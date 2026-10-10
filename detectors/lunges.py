from core.base_exercise import BaseExercise


class LungesDetector(BaseExercise):
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_SHOULDER = 12
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        sides = (
            (self.LEFT_SHOULDER, self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE),
            (self.RIGHT_SHOULDER, self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE),
        )
        visible_sides = [
            side for side in sides
            if all(landmarks[index].visibility >= self.MIN_VISIBILITY for index in side)
        ]
        candidates = visible_sides or list(sides)
        side = min(
            candidates,
            key=lambda indices: self.calculate_angle(
                self.get_point(landmarks, indices[1]),
                self.get_point(landmarks, indices[2]),
                self.get_point(landmarks, indices[3]),
            ),
        )
        shoulder_idx, hip_idx, knee_idx, ankle_idx = side

        front_knee_angle = self.calculate_angle(
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
            self.get_point(landmarks, ankle_idx),
        )
        torso_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        if side in visible_sides:
            if front_knee_angle <= self.DOWN_THRESHOLD:
                self.stage = "down"
            elif front_knee_angle >= self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

        balance_status = "STABLE" if torso_angle >= 145 else "LEANING"

        return {
            "reps": self.reps,
            "front_knee_angle": int(front_knee_angle),
            "torso_angle": int(torso_angle),
            "balance_status": balance_status,
        }
    