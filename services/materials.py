# services/materials.py
"""教材管理サービス"""

import datetime
import uuid

from services.gsheet import GSheetService


class MaterialsService:
    """教材マスタへのアクセスを行うサービス"""

    SHEET_NAME = "materials"

    @classmethod
    def _get_worksheet(cls):
        """ワークシートを取得"""
        sh = GSheetService.open_sheet()
        try:
            return sh.worksheet(cls.SHEET_NAME)
        except Exception:
            # シートが無ければ作成
            ws = sh.add_worksheet(title=cls.SHEET_NAME, rows=1000, cols=10)
            # ヘッダ行を追加
            ws.update(
                "A1:H1",
                [
                    [
                        "material_id",
                        "user_id",
                        "name",
                        "subject",
                        "description",
                        "image_url",
                        "created_at",
                        "is_active",
                    ]
                ],
            )
            return ws

    @classmethod
    def get_user_materials(cls, user_id: str) -> list:
        """指定ユーザーの教材リストを取得"""
        ws = cls._get_worksheet()
        records = ws.get_all_records()

        materials = []
        for r in records:
            # is_activeがFALSEなら除外
            if r.get("is_active", "TRUE") == "FALSE":
                continue
            if r.get("user_id") == user_id:
                materials.append(
                    {
                        "material_id": r.get("material_id"),
                        "user_id": r.get("user_id"),
                        "name": r.get("name"),
                        "subject": r.get("subject"),
                        "description": r.get("description"),
                        "image_url": r.get("image_url"),
                        "created_at": r.get("created_at"),
                    }
                )
        return materials

    @classmethod
    def add_material(
        cls,
        user_id: str,
        name: str,
        subject: str = "",
        description: str = "",
        image_url: str = "",
    ) -> tuple:
        """教材を追加
        
        Returns:
            (True, material_id) or (False, error_message)
        """
        if not user_id or not name:
            return (False, "user_id and name are required")

        ws = cls._get_worksheet()

        material_id = f"mat_{uuid.uuid4().hex[:8]}"
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            material_id,
            user_id,
            name,
            subject,
            description,
            image_url,
            created_at,
            "TRUE",
        ]

        ws.append_row(row)
        return (True, material_id)

    @classmethod
    def delete_material(cls, material_id: str, user_id: str) -> tuple:
        """教材を論理削除（is_activeをFALSEに）
        
        Returns:
            (True, None) or (False, error_message)
        """
        ws = cls._get_worksheet()
        records = ws.get_all_records()

        for idx, r in enumerate(records):
            if r.get("material_id") == material_id:
                # 所有者チェック
                if r.get("user_id") != user_id:
                    return (False, "Not authorized")
                # is_activeをFALSEに（H列 = 8列目）
                ws.update_cell(idx + 2, 8, "FALSE")  # +2 はヘッダ+0-index
                return (True, None)

        return (False, "Material not found")

    @classmethod
    def get_all_materials(cls) -> list:
        """全教材リストを取得（管理用）"""
        ws = cls._get_worksheet()
        records = ws.get_all_records()
        return [r for r in records if r.get("is_active", "TRUE") != "FALSE"]
