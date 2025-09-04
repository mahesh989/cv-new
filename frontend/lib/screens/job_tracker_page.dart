import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

class JobTrackerPage extends StatefulWidget {
  const JobTrackerPage({super.key});
  @override
  State<JobTrackerPage> createState() => _JobTrackerPageState();
}

class _JobTrackerPageState extends State<JobTrackerPage> {
  List<Map<String, dynamic>> jobs = [];

  @override
  void initState() {
    super.initState();
    _fetchJobs();
  }

  Future<void> _fetchJobs() async {
    final res = await http.get(Uri.parse('http://localhost:8000/list-jobs/'));
    if (res.statusCode == 200) {
      setState(
          () => jobs = List<Map<String, dynamic>>.from(json.decode(res.body)));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Saved Job Applications")),
      body: jobs.isEmpty
          ? const Center(child: Text("No saved jobs yet."))
          : SingleChildScrollView(
              child: DataTable(columns: const [
                DataColumn(label: Text("S.N.")),
                DataColumn(label: Text("Company")),
                DataColumn(label: Text("Phone")),
                DataColumn(label: Text("Date")),
                DataColumn(label: Text("Link")),
                DataColumn(label: Text("CV")),
              ], rows: [
                for (int i = 0; i < jobs.length; i++)
                  DataRow(cells: [
                    DataCell(Text((i + 1).toString())),
                    DataCell(Text(jobs[i]['company_name'])),
                    DataCell(Text(jobs[i]['phone'])),
                    DataCell(Text(jobs[i]['date_applied'])),
                    DataCell(IconButton(
                      icon: const Icon(Icons.link),
                      onPressed: () =>
                          launchUrl(Uri.parse(jobs[i]['job_link'])),
                    )),
                    DataCell(IconButton(
                      icon: const Icon(Icons.download),
                      onPressed: () => launchUrl(Uri.parse(
                          "http://localhost:8000${jobs[i]['tailored_cv']}")),
                    )),
                  ])
              ]),
            ),
    );
  }
}
