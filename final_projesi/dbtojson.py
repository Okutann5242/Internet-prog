# dbtojson.py

import os
import json
from app import app, db, User, Talep

def export_data_to_json():
    with app.app_context():
        users = User.query.all()
        talepler = Talep.query.all()

        data = {
            "users": [
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "is_admin": u.is_admin,
                } for u in users
            ],
            "talepler": [
                {
                    "id": t.id,
                    "subject": t.subject,
                    "description": t.description,
                    "priority": t.priority,
                    "tags": t.tags,
                    "reply": t.reply,
                    "created_at": t.created_at.isoformat(),
                    "kullanici_id": t.kullanici_id,
                } for t in talepler
            ]
        }

        file_path = os.path.join(os.path.dirname(__file__), "veri_aktarimi.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"JSON dosyası başarıyla oluşturuldu: {file_path}")

if __name__ == "__main__":
    export_data_to_json()
