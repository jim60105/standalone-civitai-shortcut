"""Monitoring and performance statistics for the HTTP client."""

import time
from typing import Dict

import gradio as gr

from .http_client import OptimizedHTTPClient
from . import setting


# Module-level monitor and HTTP client instances
_http_monitor = None
_optimized_client = None


def get_http_monitor():
    """Get or create the HTTP client performance monitor."""
    global _http_monitor
    if _http_monitor is None:
        _http_monitor = HTTPClientMonitor()
    return _http_monitor


def get_http_client():
    """Get or create the optimized HTTP client for monitoring."""
    global _optimized_client
    if _optimized_client is None:
        _optimized_client = OptimizedHTTPClient(
            api_key=setting.civitai_api_key,
            timeout=setting.http_timeout,
            max_retries=setting.http_max_retries,
        )
    else:
        if _optimized_client.api_key != setting.civitai_api_key:
            _optimized_client.update_api_key(setting.civitai_api_key)
    return _optimized_client


class HTTPClientMonitor:
    """Monitor HTTP client performance and collect statistics."""

    def __init__(self):
        self.stats: Dict = {
            'requests_by_hour': {},
            'download_speeds': [],
            'response_times': [],
            'bandwidth_usage': 0,
            'cache_hit_rate': 0,
        }
        self.start_time = time.time()

    def record_request(
        self,
        url: str,
        method: str,
        status_code: int,
        response_time: float,
        bytes_transferred: int = 0,
    ):
        """Record a request event for statistics."""
        current_hour = time.strftime('%Y-%m-%d %H:00:00')
        hour_stats = self.stats['requests_by_hour'].setdefault(
            current_hour, {'total': 0, 'success': 0, 'error': 0}
        )
        hour_stats['total'] += 1
        if status_code < 400:
            hour_stats['success'] += 1
        else:
            hour_stats['error'] += 1

        self.stats['response_times'].append(response_time)
        if len(self.stats['response_times']) > 1000:
            self.stats['response_times'] = self.stats['response_times'][-1000:]

        self.stats['bandwidth_usage'] += bytes_transferred
        if bytes_transferred > 0 and response_time > 0:
            speed = bytes_transferred / response_time
            self.stats['download_speeds'].append(speed)
            if len(self.stats['download_speeds']) > 100:
                self.stats['download_speeds'] = self.stats['download_speeds'][-100:]

    def get_performance_report(self) -> Dict:
        """Generate a summarized performance report."""
        now = time.time()
        uptime = now - self.start_time
        resp = (
            sum(self.stats['response_times']) / len(self.stats['response_times'])
            if self.stats['response_times']
            else 0
        )
        down = (
            sum(self.stats['download_speeds']) / len(self.stats['download_speeds'])
            if self.stats['download_speeds']
            else 0
        )
        total = sum(h['total'] for h in self.stats['requests_by_hour'].values())
        errors = sum(h['error'] for h in self.stats['requests_by_hour'].values())
        error_rate = (errors / total * 100) if total else 0

        return {
            'uptime_seconds': uptime,
            'total_requests': total,
            'error_rate_percent': error_rate,
            'avg_response_time_ms': resp * 1000,
            'avg_download_speed_mbps': down / 1024 / 1024 * 8,
            'total_bandwidth_mb': self.stats['bandwidth_usage'] / 1024 / 1024,
            'requests_per_minute': total / (uptime / 60) if uptime else 0,
        }


def create_monitoring_ui():
    """Create a Gradio interface for real-time HTTP client monitoring."""

    def get_status_info():
        monitor = get_http_monitor()
        report = monitor.get_performance_report()
        return (
            f"### HTTP Client Monitoring\n"
            f"**Uptime**: {report['uptime_seconds']:.0f} sec\n"
            f"**Total Requests**: {report['total_requests']}\n"
            f"**Error Rate**: {report['error_rate_percent']:.2f}%\n"
            f"**Avg Response Time**: {report['avg_response_time_ms']:.1f} ms\n"
            f"**Avg Download Speed**: {report['avg_download_speed_mbps']:.2f} Mbps\n"
            f"**Total Bandwidth**: {report['total_bandwidth_mb']:.2f} MB\n"
            f"**Requests/Min**: {report['requests_per_minute']:.1f}\n"
        )

    def get_error_statistics():
        client = get_http_client()
        errors = getattr(client, '_stats', {}).get('error_counts', {})
        if errors:
            text = "### Error Statistics\n\n"
            for k, v in sorted(errors.items()):
                text += f"**{k}**: {v}\n"
            return text
        return "### Error Statistics\n\nNo errors recorded ✅"

    def clear_statistics():
        client = get_http_client()
        if hasattr(client, '_stats'):
            with client._stats_lock:
                client._stats = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'total_bytes_downloaded': 0,
                    'total_time_spent': 0,
                    'error_counts': {},
                    'active_downloads': {},
                    'request_history': [],
                }
        monitor = get_http_monitor()
        monitor.stats = {
            'requests_by_hour': {},
            'download_speeds': [],
            'response_times': [],
            'bandwidth_usage': 0,
            'cache_hit_rate': 0,
        }
        return "Statistics cleared ✅"

    with gr.Blocks(title="HTTP Client Monitor") as ui:
        gr.Markdown("## HTTP Client Monitor Panel")
        with gr.Row():
            with gr.Column():
                status_md = gr.Markdown(get_status_info())
                btn_refresh = gr.Button("Refresh Status", variant="primary")
            with gr.Column():
                error_md = gr.Markdown(get_error_statistics())
                btn_clear = gr.Button("Clear Statistics", variant="secondary")
        btn_refresh.click(fn=get_status_info, outputs=[status_md])
        btn_refresh.click(fn=get_error_statistics, outputs=[error_md])
        btn_clear.click(fn=clear_statistics, outputs=[])
    return ui
