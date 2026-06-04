import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import SessionLocal
from app.models import (
    DocType,
    Generation,
    GenStatus,
    GenType,
    Product,
    Project,
    ProjectDocument,
    ProjectStatus,
    Segment,
    SourceFormat,
    User,
    UserRole,
)


def main() -> None:
    db = SessionLocal()
    try:
        user = User(telegram_id=123456789, name="Akmal Admin", role=UserRole.admin)
        db.add(user)
        db.flush()

        project = Project(
            owner_id=user.id,
            name="Quadro Launch 2024",
            client_name="ООО Рога и Копыта",
            status=ProjectStatus.active,
        )
        db.add(project)
        db.flush()

        segment = Segment(
            project_id=project.id,
            name="B2B Малый бизнес",
            description="Компании до 50 сотрудников",
        )
        db.add(segment)
        db.flush()

        product = Product(
            segment_id=segment.id,
            name="Тариф Старт",
            description="Базовый маркетинговый пакет",
            price="29 900 ₽/мес",
        )
        db.add(product)
        db.flush()

        document = ProjectDocument(
            project_id=project.id,
            doc_type=DocType.swot,
            title="SWOT-анализ 2024",
            original_filename="swot_2024.docx",
            file_path="uploads/swot_2024.docx",
            source_format=SourceFormat.docx,
            extracted_text="# SWOT\n## Сильные стороны\n- Опытная команда\n",
        )
        db.add(document)
        db.flush()

        generation = Generation(
            project_id=project.id,
            segment_id=segment.id,
            product_id=product.id,
            gen_type=GenType.offer,
            brief="Оффер для малого бизнеса, упор на экономию времени",
            variants=["Вариант А: ...", "Вариант Б: ..."],
            selected_variant_index=0,
            status=GenStatus.draft,
        )
        db.add(generation)
        db.commit()

        print("=== Созданные записи ===")
        u = db.get(User, user.id)
        print(f"User       | id={u.id} tg={u.telegram_id} name={u.name!r} role={u.role.value}")

        p = db.get(Project, project.id)
        print(f"Project    | id={p.id} name={p.name!r} owner_id={p.owner_id} status={p.status.value}")

        s = db.get(Segment, segment.id)
        print(f"Segment    | id={s.id} name={s.name!r} project_id={s.project_id}")

        pr = db.get(Product, product.id)
        print(f"Product    | id={pr.id} name={pr.name!r} price={pr.price!r} segment_id={pr.segment_id}")

        doc = db.get(ProjectDocument, document.id)
        print(f"Document   | id={doc.id} type={doc.doc_type.value} title={doc.title!r} project_id={doc.project_id}")

        gen = db.get(Generation, generation.id)
        print(f"Generation | id={gen.id} type={gen.gen_type.value} status={gen.status.value} variants={gen.variants}")

        print("\n=== Связи ===")
        print(f"user.projects      -> {[x.name for x in u.projects]}")
        print(f"project.segments   -> {[x.name for x in p.segments]}")
        print(f"project.documents  -> {[x.title for x in p.documents]}")
        print(f"project.generations-> {[x.id for x in p.generations]}")
        print(f"segment.products   -> {[x.name for x in s.products]}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
