import os
import sys

# Add workspace to path
sys.path.append(r"C:\Users\hinsh\Desktop\myastro")

from shared.astro.face_vision import analyze_face

def main():
    downloads = r"C:\Users\hinsh\Downloads"
    print("Scanning all images in Downloads...")
    for f in os.listdir(downloads):
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            p = os.path.join(downloads, f)
            try:
                with open(p, "rb") as img_f:
                    img_bytes = img_f.read()
                analysis = analyze_face(img_bytes)
                if analysis.get("face_found"):
                    pose = analysis.get("pose_metrics")
                    issues = analysis.get("pose_issues")
                    print(f"File: {f}")
                    print(f"  Pose Metrics: {pose}")
                    print(f"  Pose Issues: {issues}")
            except Exception as e:
                print(f"  Error reading {f}: {e}")

if __name__ == "__main__":
    main()
