package com.reportes.offline

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File

class MainActivity : AppCompatActivity() {

    private var lastReportPath: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        val statusText = findViewById<TextView>(R.id.txtStatus)
        val shareButton = findViewById<Button>(R.id.btnShare)

        findViewById<Button>(R.id.btnInspection).setOnClickListener {
            val reportPath = generateReport("inspection")
            lastReportPath = reportPath
            shareButton.isEnabled = reportPath != null
            statusText.text = reportPath?.let { "Reporte generado en:\n$it" }
                ?: "No fue posible generar el reporte de inspección"
        }

        findViewById<Button>(R.id.btnActivities).setOnClickListener {
            val reportPath = generateReport("activities")
            lastReportPath = reportPath
            shareButton.isEnabled = reportPath != null
            statusText.text = reportPath?.let { "Reporte generado en:\n$it" }
                ?: "No fue posible generar el reporte de actividades"
        }

        shareButton.setOnClickListener {
            shareLastReport()
        }
    }

    private fun generateReport(reportType: String): String? {
        return try {
            val python = Python.getInstance()
            val module = python.getModule("report_generator")

            val templateName = if (reportType == "inspection") "reporte.docx" else "reporte2.docx"
            val templateFile = copyTemplateToInternalStorage(templateName)

            val outputDir = getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS)
                ?: filesDir

            val result: PyObject = module.callAttr(
                "generate_report",
                reportType,
                templateFile.absolutePath,
                outputDir.absolutePath
            )
            result.toString()
        } catch (_: Exception) {
            null
        }
    }

    private fun copyTemplateToInternalStorage(templateName: String): File {
        val destDir = File(filesDir, "templates")
        if (!destDir.exists()) {
            destDir.mkdirs()
        }

        val destination = File(destDir, templateName)
        if (!destination.exists()) {
            assets.open("templates/$templateName").use { input ->
                destination.outputStream().use { output ->
                    input.copyTo(output)
                }
            }
        }

        return destination
    }

    private fun shareLastReport() {
        val reportPath = lastReportPath ?: return
        val reportFile = File(reportPath)
        if (!reportFile.exists()) return

        val contentUri: Uri = FileProvider.getUriForFile(
            this,
            "$packageName.provider",
            reportFile
        )

        val shareIntent = Intent(Intent.ACTION_SEND).apply {
            type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            putExtra(Intent.EXTRA_STREAM, contentUri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

        startActivity(Intent.createChooser(shareIntent, "Compartir reporte"))
    }
}
