package com.xlzhen.windowsmonitor;

import android.annotation.SuppressLint;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JsResult;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // 1. 设置全屏模式（隐藏状态栏和导航栏）
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |          // 沉浸式粘性模式
                        View.SYSTEM_UI_FLAG_FULLSCREEN |                // 全屏
                        View.SYSTEM_UI_FLAG_HIDE_NAVIGATION             // 隐藏导航栏
        );

        // 2. 保持屏幕常亮
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        WebView webView = findViewById(R.id.main_web_view);
        webView.getSettings().setJavaScriptEnabled(true);

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onJsAlert(WebView view, String url, String message, JsResult result) {
                // 使用原生 AlertDialog 显示 JavaScript 的 alert
                new AlertDialog.Builder(MainActivity.this)
                        .setTitle("提示") // 可自定义标题
                        .setMessage(message) // JavaScript 传递的消息
                        .setPositiveButton("确定", (dialog, which) -> {
                            // 必须调用 confirm() 通知 WebView 继续执行
                            result.confirm();
                        })
                        .setCancelable(false) // 阻止用户点击外部关闭
                        .create()
                        .show();

                // 返回 true 表示已处理弹窗
                return true;
            }
        });

        webView.loadUrl("http://192.168.2.124:5000");
    }

    // 处理用户返回时的全屏恢复
    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            getWindow().getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                            View.SYSTEM_UI_FLAG_FULLSCREEN |
                            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            );
        }
    }
}