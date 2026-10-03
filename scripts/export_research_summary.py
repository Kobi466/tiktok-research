"""Truthful Markdown research summary exporter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.research_io import (
    load_definitions,
    processed_csv_path,
    read_csv_records,
    utc_now,
)

TABLE_NAMES = (
    "sources",
    "observations",
    "products",
    "competitors",
    "videos",
    "findings",
    "hypotheses",
    "audit_findings",
)


def _get_definitions(root: Path) -> dict:
    """Load canonical definitions from workspace or fallback to project root."""
    workspace_config = Path(root) / "config" / "field-definitions.json"
    if workspace_config.is_file():
        return load_definitions(root)
    return load_definitions(_PROJECT_ROOT)


def _clean_cell(value: Any) -> str:
    """Escape Markdown pipe and newline characters for table cells."""
    if value is None:
        return ""
    text = str(value).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    text = text.replace("|", "\\|")
    return text.strip()


def _load_table_records(root: Path, table_name: str) -> list[dict[str, str]]:
    """Read processed CSV records or return empty list if missing or zero bytes."""
    csv_path = processed_csv_path(root, table_name)
    if not csv_path.exists():
        return []
    if csv_path.is_dir():
        raise IsADirectoryError(f"Expected CSV file but found directory: {csv_path}")
    if csv_path.stat().st_size == 0:
        return []
    return read_csv_records(csv_path)


def export_summary(
    root: Path,
    output: Path,
    title: str,
    accessed_at: str | None = None,
) -> Path:
    """Export a truthful Markdown research summary from processed canonical data."""
    resolved_root = Path(root).expanduser().resolve()
    out_path = Path(output).expanduser()
    if not out_path.is_absolute():
        resolved_output = (resolved_root / out_path).resolve()
    else:
        resolved_output = out_path.resolve()

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    report_time = accessed_at if accessed_at else utc_now()

    # Read records from all 8 canonical tables
    sources = _load_table_records(resolved_root, "sources")
    observations = _load_table_records(resolved_root, "observations")
    products = _load_table_records(resolved_root, "products")
    competitors = _load_table_records(resolved_root, "competitors")
    videos = _load_table_records(resolved_root, "videos")
    findings = _load_table_records(resolved_root, "findings")
    hypotheses = _load_table_records(resolved_root, "hypotheses")
    audit_findings = _load_table_records(resolved_root, "audit_findings")

    # Deterministic sorting by primary ID
    sorted_sources = sorted(sources, key=lambda r: r.get("source_id", ""))
    sorted_observations = sorted(observations, key=lambda r: r.get("observation_id", ""))
    sorted_products = sorted(products, key=lambda r: r.get("product_id", ""))
    sorted_competitors = sorted(competitors, key=lambda r: r.get("competitor_id", ""))
    sorted_videos = sorted(videos, key=lambda r: r.get("video_id", ""))
    sorted_findings = sorted(findings, key=lambda r: r.get("finding_id", ""))
    sorted_hypotheses = sorted(hypotheses, key=lambda r: r.get("hypothesis_id", ""))
    sorted_audit_findings = sorted(audit_findings, key=lambda r: r.get("audit_id", ""))

    # Separate verified findings from hypotheses / draft findings
    verified_findings = [
        f
        for f in sorted_findings
        if f.get("evidence_type") in ("direct_source", "calculated", "estimate")
        and f.get("status") in ("audited", "accepted", "verified")
    ]
    unverified_findings = [
        f
        for f in sorted_findings
        if f.get("evidence_type") == "hypothesis"
        or f.get("status") in ("draft", "hypothesis")
    ]

    lines: list[str] = []

    # 1. Title & metadata
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- **Thời điểm xuất báo cáo:** {report_time}")
    lines.append(f"- **Thư mục dữ liệu:** {resolved_root}")
    lines.append("")

    # 2. Tóm tắt phạm vi và phương pháp
    lines.append("## Tóm tắt phạm vi và phương pháp")
    lines.append("")
    lines.append(
        "- **Phương pháp thu thập:** Chỉ sử dụng dữ liệu công khai có thể kiểm chứng; "
        "tôn trọng điều khoản dịch vụ và ranh giới quyền riêng tư."
    )
    lines.append(
        "- **Nguyên tắc cốt lõi:** Tuyệt đối không suy đoán doanh số, doanh thu, GMV "
        "hay tỷ lệ chuyển đổi từ các chỉ số tương tác video (lượt xem, thích, bình luận)."
    )
    lines.append(
        "- **Phân tách bằng chứng:** Phân định nghiêm ngặt giữa dữ kiện có bằng chứng "
        "(`direct_source`, `calculated`, `estimate`) và các giả thuyết chưa xác minh (`hypothesis`)."
    )
    lines.append("")
    if not verified_findings and not sorted_sources and not sorted_products and not sorted_videos:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        lines.append(
            f"Tổng quan phạm vi: {len(sorted_sources)} nguồn dữ liệu, "
            f"{len(sorted_products)} sản phẩm, {len(sorted_videos)} video quan sát, "
            f"{len(verified_findings)} phát hiện có bằng chứng."
        )
        lines.append("")

    # 3. Nguồn thông tin đã sử dụng
    lines.append("## Nguồn thông tin đã sử dụng")
    lines.append("")
    if not sorted_sources:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        lines.append(
            "| Mã nguồn | Tiêu đề | URL | Đơn vị xuất bản | Loại nguồn | Trạng thái truy cập | Thời điểm truy cập |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for s in sorted_sources:
            sid = _clean_cell(s.get("source_id"))
            stitle = _clean_cell(s.get("title"))
            surl = _clean_cell(s.get("url"))
            spub = _clean_cell(s.get("publisher"))
            stype = _clean_cell(s.get("source_type"))
            sstatus = _clean_cell(s.get("access_status"))
            sacc = _clean_cell(s.get("accessed_at"))
            lines.append(
                f"| {sid} | {stitle} | {surl} | {spub} | {stype} | {sstatus} | {sacc} |"
            )
        lines.append("")

    # 4. Phát hiện có bằng chứng
    lines.append("## Phát hiện có bằng chứng")
    lines.append("")
    if not verified_findings:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        lines.append(
            "| Mã phát hiện | Nội dung phát hiện | Loại bằng chứng | Độ tin cậy | Nguồn tham chiếu | Phương pháp tính toán |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for f in verified_findings:
            fid = _clean_cell(f.get("finding_id"))
            ftext = _clean_cell(f.get("finding_text"))
            fevid = _clean_cell(f.get("evidence_type"))
            fconf = _clean_cell(f.get("confidence"))
            fsrc = _clean_cell(f.get("source_ids"))
            fcalc = _clean_cell(f.get("calculation_method") or "-")
            lines.append(f"| {fid} | {ftext} | {fevid} | {fconf} | {fsrc} | {fcalc} |")
        lines.append("")

    # 5. Sản phẩm và nhóm sản phẩm
    lines.append("## Sản phẩm và nhóm sản phẩm")
    lines.append("")
    if not sorted_products:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        lines.append(
            "| Mã SP | Tên sản phẩm | Danh mục | Người bán | Giá niêm yết | Hoa hồng | Loại bằng chứng | Độ tin cậy |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for p in sorted_products:
            pid = _clean_cell(p.get("product_id"))
            pname = _clean_cell(p.get("product_name"))
            pcat = _clean_cell(p.get("category"))
            pseller = _clean_cell(p.get("seller_name"))

            # Price formatting: never invent 0 or numeric value
            price_val = (p.get("price_value") or "").strip()
            currency = (p.get("currency") or "").strip()
            if not price_val:
                price_display = "Chưa có giá xác minh"
            else:
                price_display = f"{price_val} {currency}".strip()

            # Commission formatting
            comm_val = (p.get("commission_value") or "").strip()
            comm_type = (p.get("commission_type") or "").strip()
            comm_src = (p.get("commission_source_id") or "").strip()
            if comm_val:
                parts = [comm_val]
                if comm_type:
                    parts.append(f"({comm_type})")
                if comm_src:
                    parts.append(f"[Nguồn: {comm_src}]")
                commission_display = " ".join(parts)
            else:
                commission_display = "-"

            pevid = _clean_cell(p.get("evidence_type"))
            pconf = _clean_cell(p.get("confidence"))
            lines.append(
                f"| {pid} | {pname} | {pcat} | {pseller} | "
                f"{_clean_cell(price_display)} | {_clean_cell(commission_display)} | "
                f"{pevid} | {pconf} |"
            )
        lines.append("")

        # Optional product comparison details (customer problem, benefits, competition, video potential)
        has_comparison = any(
            p.get("customer_problem")
            or p.get("benefits_observed")
            or p.get("video_potential")
            or p.get("competition_notes")
            for p in sorted_products
        )
        if has_comparison:
            lines.append("### Bảng so sánh sản phẩm chi tiết")
            lines.append("")
            lines.append(
                "| Mã SP | Tên sản phẩm | Vấn đề khách hàng | Lợi ích ghi nhận | Ghi chú cạnh tranh | Tiềm năng làm video |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- |")
            for p in sorted_products:
                pid = _clean_cell(p.get("product_id"))
                pname = _clean_cell(p.get("product_name"))
                prob = _clean_cell(p.get("customer_problem") or "-")
                ben = _clean_cell(p.get("benefits_observed") or "-")
                comp = _clean_cell(p.get("competition_notes") or "-")
                pot = _clean_cell(p.get("video_potential") or "-")
                lines.append(f"| {pid} | {pname} | {prob} | {ben} | {comp} | {pot} |")
            lines.append("")

    # 6. Dữ liệu video/kênh công khai
    lines.append("## Dữ liệu video/kênh công khai")
    lines.append("")
    if not sorted_videos and not sorted_competitors:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        lines.append(
            "*Lưu ý về phương pháp: Các chỉ số video công khai (views, likes, comments) "
            "được ghi nhận tại thời điểm quan sát cụ thể (observed_at). Tuyệt đối không suy đoán "
            "doanh số, doanh thu, GMV hay tỷ lệ chuyển đổi từ các chỉ số này.*"
        )
        lines.append("")
        if sorted_videos:
            lines.append(
                "| Mã video | Kênh / Đối thủ | URL video | Lượt xem | Lượt thích | Bình luận | "
                "Thời điểm quan sát (observed_at) | Loại bằng chứng |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
            for v in sorted_videos:
                vid = _clean_cell(v.get("video_id"))
                vcmp = _clean_cell(v.get("competitor_id"))
                vurl = _clean_cell(v.get("video_url"))
                vviews = _clean_cell(v.get("views_observed") or "-")
                vlikes = _clean_cell(v.get("likes_observed") or "-")
                vcomments = _clean_cell(v.get("comments_observed") or "-")
                vobs = _clean_cell(v.get("observed_at"))
                vevid = _clean_cell(v.get("evidence_type"))
                lines.append(
                    f"| {vid} | {vcmp} | {vurl} | {vviews} | {vlikes} | {vcomments} | {vobs} | {vevid} |"
                )
            lines.append("")

            has_video_analysis = any(
                v.get("hook_observed")
                or v.get("story_structure")
                or v.get("product_presentation")
                or v.get("call_to_action")
                or v.get("affiliate_disclosure")
                for v in sorted_videos
            )
            if has_video_analysis:
                lines.append("### Phân tích nội dung và kịch bản video đối thủ")
                lines.append("")
                lines.append(
                    "| Mã video | Kênh / Đối thủ | Hook quan sát | Cấu trúc câu chuyện | Trình bày sản phẩm | Kêu gọi hành động (CTA) | Khai báo tiếp thị liên kết |"
                )
                lines.append("| --- | --- | --- | --- | --- | --- | --- |")
                for v in sorted_videos:
                    vid = _clean_cell(v.get("video_id"))
                    vcmp = _clean_cell(v.get("competitor_id"))
                    vhook = _clean_cell(v.get("hook_observed") or "-")
                    vstory = _clean_cell(v.get("story_structure") or "-")
                    vpres = _clean_cell(v.get("product_presentation") or "-")
                    vcta = _clean_cell(v.get("call_to_action") or "-")
                    vdisc = _clean_cell(v.get("affiliate_disclosure") or "-")
                    lines.append(
                        f"| {vid} | {vcmp} | {vhook} | {vstory} | {vpres} | {vcta} | {vdisc} |"
                    )
                lines.append("")
        if sorted_competitors:
            lines.append("### Danh sách kênh / đối thủ quan sát")
            lines.append("")
            lines.append(
                "| Mã kênh | Nền tảng | Kênh / Tên | Lĩnh vực | URL hồ sơ | Thời điểm quan sát (observed_at) |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- |")
            for c in sorted_competitors:
                cid = _clean_cell(c.get("competitor_id"))
                cplat = _clean_cell(c.get("platform"))
                chandle = _clean_cell(c.get("handle_or_name"))
                cniche = _clean_cell(c.get("niche"))
                curl = _clean_cell(c.get("profile_url"))
                cobs = _clean_cell(c.get("observed_at"))
                lines.append(f"| {cid} | {cplat} | {chandle} | {cniche} | {curl} | {cobs} |")
            lines.append("")

    # 7. Giả thuyết chưa xác minh
    lines.append("## Giả thuyết chưa xác minh")
    lines.append("")
    if not sorted_hypotheses and not unverified_findings:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        if sorted_hypotheses:
            lines.append("### Giả thuyết nghiên cứu")
            lines.append("")
            lines.append(
                "| Mã giả thuyết | Nội dung giả thuyết | Đối tượng mục tiêu | "
                "Thử nghiệm đề xuất | Chỉ số thành công | Dữ liệu cần có | Trạng thái |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- | --- |")
            for h in sorted_hypotheses:
                hid = _clean_cell(h.get("hypothesis_id"))
                hhyp = _clean_cell(h.get("hypothesis"))
                htarget = _clean_cell(h.get("target_audience"))
                htest = _clean_cell(h.get("proposed_test"))
                hmetric = _clean_cell(h.get("success_metric"))
                hreq = _clean_cell(h.get("required_data"))
                hstat = _clean_cell(h.get("status"))
                lines.append(
                    f"| {hid} | {hhyp} | {htarget} | {htest} | {hmetric} | {hreq} | {hstat} |"
                )
            lines.append("")
        if unverified_findings:
            lines.append("### Nhận định dạng giả thuyết hoặc dự thảo chưa qua kiểm toán")
            lines.append("")
            lines.append(
                "| Mã phát hiện | Nội dung nhận định | Loại bằng chứng | Trạng thái | Ghi chú / Giới hạn |"
            )
            lines.append("| --- | --- | --- | --- | --- |")
            for f in unverified_findings:
                fid = _clean_cell(f.get("finding_id"))
                ftext = _clean_cell(f.get("finding_text"))
                fevid = _clean_cell(f.get("evidence_type"))
                fstat = _clean_cell(f.get("status"))
                flim = _clean_cell(f.get("limitations"))
                lines.append(f"| {fid} | {ftext} | {fevid} | {fstat} | {flim} |")
            lines.append("")

    # 8. Dữ liệu cần thu thập tiếp
    lines.append("## Dữ liệu cần thu thập tiếp")
    lines.append("")
    next_data_items: list[str] = []
    for h in sorted_hypotheses:
        req = (h.get("required_data") or "").strip()
        test = (h.get("proposed_test") or "").strip()
        hid = (h.get("hypothesis_id") or "").strip()
        hyp = (h.get("hypothesis") or "").strip()
        if req or test:
            desc = f"- **[{hid}]** {hyp} — Dữ liệu cần thu thập: {req or 'Chưa xác định'}"
            if test:
                desc += f" (Thử nghiệm đề xuất: {test})"
            next_data_items.append(desc)

    for a in sorted_audit_findings:
        act = (a.get("recommended_action") or "").strip()
        if act:
            aid = (a.get("audit_id") or "").strip()
            next_data_items.append(f"- **[Kiểm toán {aid}]** Hành động bổ sung: {act}")

    if not next_data_items:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        for item in next_data_items:
            lines.append(item)
        lines.append("")

    # 9. Giới hạn và rủi ro
    lines.append("## Giới hạn và rủi ro")
    lines.append("")
    lines.append(
        "- **Ranh giới an toàn và quyền riêng tư:** Nghiên cứu tuyệt đối không sử dụng công cụ vượt rào cản kỹ thuật, "
        "không xâm nhập API riêng tư và không thu thập thông tin định danh cá nhân."
    )
    lines.append(
        "- **Giới hạn số liệu thương mại:** Không suy đoán doanh số thực tế, doanh thu hay tỷ lệ chuyển đổi "
        "từ lượt xem, tương tác video hoặc số lượng người theo dõi."
    )
    lines.append("")

    restricted_sources = [
        s for s in sorted_sources if s.get("access_status") in ("blocked", "partial")
    ]

    records_with_limits: list[str] = []
    for s in sorted_sources:
        if s.get("limitations") and s not in restricted_sources:
            records_with_limits.append(f"- Nguồn [{s.get('source_id')}]: {s.get('limitations')}")
    for o in sorted_observations:
        if o.get("limitations"):
            records_with_limits.append(f"- Quan sát [{o.get('observation_id')}]: {o.get('limitations')}")
    for p in sorted_products:
        if p.get("limitations"):
            records_with_limits.append(f"- Sản phẩm [{p.get('product_id')}]: {p.get('limitations')}")
    for v in sorted_videos:
        if v.get("limitations"):
            records_with_limits.append(f"- Video [{v.get('video_id')}]: {v.get('limitations')}")
    for f in sorted_findings:
        if f.get("limitations"):
            records_with_limits.append(f"- Phát hiện [{f.get('finding_id')}]: {f.get('limitations')}")
    for h in sorted_hypotheses:
        if h.get("limitations"):
            records_with_limits.append(f"- Giả thuyết [{h.get('hypothesis_id')}]: {h.get('limitations')}")

    if restricted_sources:
        lines.append("### Nguồn bị chặn hoặc hạn chế truy cập")
        lines.append("")
        for s in restricted_sources:
            sid = s.get("source_id", "")
            url = s.get("url", "")
            status = s.get("access_status", "")
            lim = s.get("limitations") or "Nguồn không thể truy cập công khai"
            lines.append(f"- Nguồn **[{sid}]** ({url}) - Trạng thái: `{status}`. Giới hạn: {lim}")
        lines.append("")

    if records_with_limits:
        lines.append("### Giới hạn ghi nhận từ các bản ghi")
        lines.append("")
        for r in records_with_limits:
            lines.append(r)
        lines.append("")

    if not restricted_sources and not records_with_limits:
        lines.append("Chưa có dữ liệu được xác minh về các giới hạn cụ thể ngoài nguyên tắc chung.")
        lines.append("")

    # 10. Kiểm toán dữ liệu
    lines.append("## Kiểm toán dữ liệu")
    lines.append("")
    lines.append("### Thống kê số lượng bản ghi")
    lines.append("")
    lines.append("| Bảng dữ liệu | Số lượng bản ghi |")
    lines.append("| --- | --- |")
    lines.append(f"| sources | {len(sources)} |")
    lines.append(f"| observations | {len(observations)} |")
    lines.append(f"| products | {len(products)} |")
    lines.append(f"| competitors | {len(competitors)} |")
    lines.append(f"| videos | {len(videos)} |")
    lines.append(f"| findings | {len(findings)} |")
    lines.append(f"| hypotheses | {len(hypotheses)} |")
    lines.append(f"| audit_findings | {len(audit_findings)} |")
    lines.append("")

    if not sorted_audit_findings:
        lines.append("Chưa có dữ liệu được xác minh.")
        lines.append("")
    else:
        lines.append("### Chi tiết kết quả kiểm toán")
        lines.append("")
        lines.append(
            "| Mã kiểm toán | Loại bản ghi | Mã bản ghi | Quy tắc | Kết quả | "
            "Vấn đề | Khuyến nghị xử lý | Thời điểm kiểm toán |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for a in sorted_audit_findings:
            aid = _clean_cell(a.get("audit_id"))
            atype = _clean_cell(a.get("record_type"))
            arid = _clean_cell(a.get("record_id"))
            arule = _clean_cell(a.get("audit_rule"))
            ares = _clean_cell(a.get("result"))
            aissue = _clean_cell(a.get("issue"))
            aact = _clean_cell(a.get("recommended_action"))
            atime = _clean_cell(a.get("audited_at"))
            lines.append(
                f"| {aid} | {atype} | {arid} | {arule} | {ares} | {aissue} | {aact} | {atime} |"
            )
        lines.append("")

    output_content = "\n".join(lines).rstrip() + "\n"
    resolved_output.write_text(output_content, encoding="utf-8")
    return resolved_output


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for exporting truthful research summary."""
    parser = argparse.ArgumentParser(
        description="Export a truthful Markdown research summary."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Target workspace root path (default: current directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Required destination path for exported Markdown file.",
    )
    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Required report title string.",
    )
    parser.add_argument(
        "--accessed-at",
        type=str,
        default=None,
        help="Optional ISO 8601 timestamp string for report generation time.",
    )

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    target_root = args.root.expanduser().resolve()
    if not target_root.exists() or not target_root.is_dir():
        sys.stderr.write(
            f"Export invocation error: root does not exist or is not a directory: {target_root}\n"
        )
        return 2

    try:
        out_path = export_summary(
            root=target_root,
            output=args.output,
            title=args.title,
            accessed_at=args.accessed_at,
        )
    except Exception as err:
        sys.stderr.write(f"Export error: {err}\n")
        return 2

    print(f"Summary exported to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
